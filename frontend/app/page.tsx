"use client"

import { useEffect, useState } from "react"

import { Calendar } from "@/components/ui/calendar"
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import clsx from "clsx"
import { Badge } from "@/components/ui/badge"

type Event = {
  id: number
  userid: number
  eventtitle: string
  startdate: string
  enddate: string
  location: string
  description: string
  attendees: string[] | null
  status: string | null
  priority: number | null
  created: string
  lastmodified: string
  organizer: string | null
  recurrencerule: string | null
  timezone: string | null
  url: string | null
  classification: string | null
  transparency: string | null
  iscompleted: boolean
  tags: string[] | null
}

type Events = Event[]

export default function IndexPage() {
  const [eventDays, setEventDays] = useState([])
  const [selectedDate, setSelectedDate] = useState<Date>()
  const [events, setEvents] = useState<Events>([])

  useEffect(() => {
    fetch("http://localhost:8001/events/brief-month", {
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
      },
    })
      .then((response) => response.json())
      .then((data) => {
        const dates = data.data.map((item: string) => new Date(item))
        setEventDays(dates)
      })
  }, [])

  const handleDayClick = async (date: Date) => {
    const adjustedDateFromISO = new Date(
      date.getTime() - date.getTimezoneOffset() * 60000
    )

    setSelectedDate(date)
    await fetch(
      `http://localhost:8001/events/date/${
        adjustedDateFromISO.toISOString().split("T")[0]
      }`
    )
      .then((response) => response.json())
      .then((data) => setEvents(data as Events))
    setScene("day")
  }

  const [scene, setScene] = useState<"calendar" | "day">("calendar")

  return (
    <section className="w-full flex justify-center pt-8">
      {scene === "calendar" ? (
        <Calendar
          className="w-full"
          disableNavigation
          modifiers={{ event: eventDays }}
          modifiersClassNames={{
            event:
              'relative after:content-[""] after:w-[3px] after:aspect-square after:bg-blue-500 after:rounded-full after:bottom-1 after:absolute',
          }}
          onDayClick={handleDayClick}
        />
      ) : (
        <div className="flex flex-col gap-4 p-4">
          <div className="text-center cursor-pointer text-accent" onClick={() => setScene('calendar')}>Назад</div>
          {events.map((event) => (
            <Card className={clsx(event.iscompleted && 'border-green-500 opacity-30')}>
              <CardHeader>
                <CardTitle>{event.eventtitle}</CardTitle>
                <CardDescription><div className="flex gap-1">{event.tags?.map((i, index) => <Badge variant='secondary' key={index}>{i}</Badge>)}</div></CardDescription>
                <CardDescription>{event.description}</CardDescription>
                <CardDescription>
                  {event.startdate} - {event.enddate}
                </CardDescription>
              </CardHeader>
            </Card>
          ))}
        </div>
      )}
    </section>
  )
}
